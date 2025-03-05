export interface CliOptions {
    query?:String,
    keywords?: string[],
    num_top_packages?: number,
    popularity_weight?: number,
    quality_weight?: number,
    maintenance_weight?: number,
}

export interface GhAnalysisResults {
    pr_results:PRInteractionsMap,
    issues_results:IssueInteractionsMap
}

export type PackageLinks = {
    npm: string;
    homepage?: string;
    repository?: string;
    bugs?: string;
};

export type Author = {
    name: string;
};

export type Publisher = {
    username: string;
    email: string;
};

export type Maintainer = {
    username: string;
    email: string;
};

export type PackageScoreDetail = {
    quality: number;
    popularity: number;
    maintenance: number;
};

export type PackageScore = {
    final: number;
    detail: PackageScoreDetail;
};

export type NpmsPackage = {
    name: string;
    scope: string;
    version: string;
    description: string;
    keywords?: string[];
    date: string; // ISO 8601 date string
    links: PackageLinks;
    author?: Author;
    publisher: Publisher;
    maintainers: Maintainer[];
};

export type SearchResult = {
    package: NpmsPackage;
    score: PackageScore;
    searchScore: number;
};

export type NpmsSearchResponse = {
    total: number;
    results: SearchResult[];
};
export type PRDetails = {
    authors: Set<string>;
    reviewers: Set<string>;
    participants: Set<string>;
    prLink: string;
};
export type IssueDetails = {
    author: string;
    participants: Set<string>;
    issueLink: string;
};
export type PRInteractionsMap = Map<string, PRDetails>;
export type IssueInteractionsMap = Map<string,IssueDetails>;
export type PRState = "closed" | "open" | "all"