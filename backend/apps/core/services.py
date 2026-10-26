"""Business logic and graph algorithms for family tree management.

Key functionalities:
1. DAG (Directed Acyclic Graph) cycle detection and ancestry validation.
2. Multi-generational hierarchical family tree builder for focal deceased person.
3. Audit logger helper.
"""

from collections import deque
from typing import Dict, List, Set, Any, Optional
from django.core.exceptions import ValidationError
from .models import DeceasedPerson, FamilyRelationship, RelationshipType, AuditLog


def get_all_ancestor_ids(person_id: int) -> Set[int]:
    """Berilgan shaxsning barcha ajdodlari (ota-onalar, bobo-buvilar, katta bobolar...) ID larini qaytaradi.
    
    BFS (Kenglik bo'yicha qidiruv) algoritmi orqali topiladi.
    """
    ancestor_ids: Set[int] = set()
    queue = deque([person_id])
    
    while queue:
        current_id = queue.popleft()
        # current_id ning barcha ota-onalarini topamiz (person=current_id, relationship=PARENT)
        parent_relations = FamilyRelationship.objects.filter(
            person_id=current_id,
            relationship_type=RelationshipType.PARENT
        ).values_list('related_person_id', flat=True)
        
        for p_id in parent_relations:
            if p_id not in ancestor_ids:
                ancestor_ids.add(p_id)
                queue.append(p_id)
                
    return ancestor_ids


def get_all_descendant_ids(person_id: int) -> Set[int]:
    """Berilgan shaxsning barcha avlodlari (bolalari, nabiralari, chevaralari...) ID larini qaytaradi.
    
    BFS algoritmi orqali topiladi.
    """
    descendant_ids: Set[int] = set()
    queue = deque([person_id])
    
    while queue:
        current_id = queue.popleft()
        # current_id ota/ona bo'lgan barcha bolalarni topamiz (related_person=current_id, relationship=PARENT)
        child_relations = FamilyRelationship.objects.filter(
            related_person_id=current_id,
            relationship_type=RelationshipType.PARENT
        ).values_list('person_id', flat=True)
        
        for c_id in child_relations:
            if c_id not in descendant_ids:
                descendant_ids.add(c_id)
                queue.append(c_id)
                
    return descendant_ids


def validate_no_ancestry_cycle(child_id: int, parent_id: int) -> None:
    """Yangi ota-ona bog'lanishida aylanma sikl (cycle) hosil bo'lmasligini tekshiradi.
    
    Mantiqiy qoidalar:
    1. Bola o'zining otasi/onasi bo'la olmaydi (child_id == parent_id).
    2. Taklif qilinayotgan ota (parent_id) allaqachon bolaning (child_id) avlodi bo'lmasligi shart.
       Agar parent_id child_id ning avlodlari orasida bo'lsa, sikl yuzaga keladi.
    3. Shuningdek, bola (child_id) allaqachon taklif qilinayotgan otaning ajdodi bo'lsa ham sikl hosil bo'ladi.
    """
    if child_id == parent_id:
        raise ValidationError("Shaxs o‘ziga o‘zi ota/ona bo‘lishi mumkin emas!")

    # 1. parent_id ning ajdodlari orasida child_id bormi?
    parent_ancestors = get_all_ancestor_ids(parent_id)
    if child_id in parent_ancestors:
        raise ValidationError(
            "Mantiqiy aylanma sikl (Cycle) aniqlandi: Tanlangan ota/onaning ajdodlari "
            "orasida ushbu shaxs allaqachon mavjud! Nasl-nasabda aylanma zanjir hosil qilish qat’iyan man etiladi."
        )

    # 2. child_id ning avlodlari orasida parent_id bormi?
    child_descendants = get_all_descendant_ids(child_id)
    if parent_id in child_descendants:
        raise ValidationError(
            "Mantiqiy xato: Siz ushbu shaxsning o‘z avlodi (bolasi yoki nabirasi)ni unga ota/ona qilib biriktirmoqchisiz!"
        )


class FamilyTreeService:
    """Markaziy marhum (focal deceased) atrofida to'liq ierarxik shajarani yig'uvchi xizmat.
    
    Qurilma strukturalari:
    - focal: Markaziy shaxs
    - paternal_ancestors: Ota tomon ajdodlar (Ota -> Bobo, Buvi -> ...)
    - maternal_ancestors: Ona tomon ajdodlar (Ona -> Bobo, Buvi -> ...)
    - spouses: Turmush o'rtoqlari
    - descendants: Bolalari va ularning bolalari (daraxt ko'rinishida)
    """

    def __init__(self, focal_person: DeceasedPerson):
        self.focal = focal_person

    @staticmethod
    def _serialize_node(person: DeceasedPerson) -> Dict[str, Any]:
        """Daraxt nodi uchun ommaviy xavfsiz ma'lumotlar."""
        photo_url = None
        if person.photo:
            try:
                photo_url = person.photo.url
            except ValueError:
                photo_url = None

        token = None
        if hasattr(person, 'qr_record') and person.qr_record.is_active:
            token = person.qr_record.public_token

        return {
            'id': person.id,
            'full_name': person.full_name,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'middle_name': person.middle_name,
            'gender': person.gender,
            'birth_year': person.birth_date.year if person.birth_date else None,
            'death_year': person.death_date.year if person.death_date else None,
            'birth_date': person.birth_date.isoformat() if person.birth_date else None,
            'death_date': person.death_date.isoformat() if person.death_date else None,
            'photo_url': photo_url,
            'cemetery_name': person.cemetery.name if person.cemetery else None,
            'grave_number': person.grave_number,
            'public_token': token,
            'biography_preview': (person.biography[:180] + '...') if len(person.biography) > 180 else person.biography,
        }

    def _get_parent_node(self, person: DeceasedPerson, target_gender: str, depth: int = 1, max_depth: int = 3) -> Optional[Dict[str, Any]]:
        """Ajdodlar ierarxiyasini rekursiv yig'ish (ota yoki ona tarmog'i)."""
        if depth > max_depth:
            return None

        # person ning ota/onalarini topamiz
        parent_rel = FamilyRelationship.objects.filter(
            person=person,
            relationship_type=RelationshipType.PARENT,
            related_person__gender=target_gender,
            related_person__is_published=True,
            related_person__is_archived=False
        ).select_related('related_person', 'related_person__cemetery', 'related_person__qr_record').first()

        if not parent_rel:
            return None

        parent_person = parent_rel.related_person
        node = self._serialize_node(parent_person)
        node['relation'] = "Ota" if target_gender == DeceasedPerson.GENDER_MALE else "Ona"
        node['depth'] = depth

        # Uning ham ota va onasini qo'shamiz (bobo va buvilar)
        father = self._get_parent_node(parent_person, DeceasedPerson.GENDER_MALE, depth + 1, max_depth)
        mother = self._get_parent_node(parent_person, DeceasedPerson.GENDER_FEMALE, depth + 1, max_depth)
        
        node['father'] = father
        node['mother'] = mother
        return node

    def _get_descendants_tree(self, person: DeceasedPerson, depth: int = 1, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Avlodlar (bolalar va nabiralar) daraxtini rekursiv yig'ish."""
        if depth > max_depth:
            return []

        # person ota/ona bo'lgan barcha bolalarni topamiz
        child_rels = FamilyRelationship.objects.filter(
            related_person=person,
            relationship_type=RelationshipType.PARENT,
            person__is_published=True,
            person__is_archived=False
        ).select_related('person', 'person__cemetery', 'person__qr_record').order_by('person__birth_date', 'person__id')

        children_nodes = []
        for rel in child_rels:
            child = rel.person
            node = self._serialize_node(child)
            node['depth'] = depth
            
            # Keyingi avlod (nabiralar)
            next_generation = self._get_descendants_tree(child, depth + 1, max_depth)
            node['children'] = next_generation
            node['children_count'] = len(next_generation)
            children_nodes.append(node)

        return children_nodes

    def _get_spouses(self) -> List[Dict[str, Any]]:
        """Turmush o'rtoqlarini topish."""
        spouses = []
        spouse_rels = FamilyRelationship.objects.filter(
            relationship_type=RelationshipType.SPOUSE,
            person=self.focal,
            related_person__is_published=True,
            related_person__is_archived=False
        ).select_related('related_person', 'related_person__cemetery', 'related_person__qr_record')

        for rel in spouse_rels:
            spouses.append(self._serialize_node(rel.related_person))

        # Teskari munosabat ham bo'lishi mumkin (related_person=focal)
        reverse_spouses = FamilyRelationship.objects.filter(
            relationship_type=RelationshipType.SPOUSE,
            related_person=self.focal,
            person__is_published=True,
            person__is_archived=False
        ).select_related('person', 'person__cemetery', 'person__qr_record')

        for rel in reverse_spouses:
            node = self._serialize_node(rel.person)
            if not any(s['id'] == node['id'] for s in spouses):
                spouses.append(node)

        return spouses

    def build_full_tree(self) -> Dict[str, Any]:
        """Markaziy marhum asosida to'liq shajara strukturasini qaytaradi."""
        focal_node = self._serialize_node(self.focal)

        paternal_tree = self._get_parent_node(self.focal, DeceasedPerson.GENDER_MALE)
        maternal_tree = self._get_parent_node(self.focal, DeceasedPerson.GENDER_FEMALE)
        spouses = self._get_spouses()
        descendants = self._get_descendants_tree(self.focal)

        return {
            'focal_person': focal_node,
            'paternal_ancestors': paternal_tree,
            'maternal_ancestors': maternal_tree,
            'spouses': spouses,
            'descendants': descendants,
            'tree_stats': {
                'has_paternal': paternal_tree is not None,
                'has_maternal': maternal_tree is not None,
                'spouses_count': len(spouses),
                'children_count': len(descendants),
            }
        }


def get_client_ip(request) -> Optional[str]:
    """Mijozning haqiqiy IP manzili.

    Nginx proksi ortida REMOTE_ADDR proksining o'z manzili bo'ladi, shuning uchun
    nginx o'rnatadigan X-Real-IP sarlavhasi ustun turadi.
    """
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')


def log_audit(action: str, user=None, ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> AuditLog:
    """Xavfsizlik va o'zgarishlar auditini xavfsiz qayd etish."""
    return AuditLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        ip_address=ip_address,
        details=details or {}
    )
