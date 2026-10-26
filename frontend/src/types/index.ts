export type GenderType = 'MALE' | 'FEMALE';

export interface CemeteryInfo {
  name: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  description: string;
}

export interface PublicDeceased {
  public_token: string;
  full_name: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  birth_date: string | null;
  death_date: string;
  years: string;
  gender: GenderType;
  photo: string | null;
  biography: string;
  cemetery: CemeteryInfo | null;
  grave_number: string;
}

export interface TreeNode {
  id: number;
  full_name: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  gender: GenderType;
  birth_year: number | null;
  death_year: number | null;
  birth_date?: string | null;
  death_date?: string | null;
  photo_url: string | null;
  cemetery_name?: string | null;
  grave_number?: string;
  public_token?: string | null;
  biography_preview?: string;
  relation?: string;
  depth?: number;
  // Ajdodlar tarmog'i
  father?: TreeNode | null;
  mother?: TreeNode | null;
  // Avlodlar tarmog'i
  children?: TreeNode[];
  children_count?: number;
}

export interface FamilyTreeData {
  focal_person: TreeNode;
  paternal_ancestors: TreeNode | null;
  maternal_ancestors: TreeNode | null;
  spouses: TreeNode[];
  descendants: TreeNode[];
  tree_stats: {
    has_paternal: boolean;
    has_maternal: boolean;
    spouses_count: number;
    children_count: number;
  };
}
