export function getRepoFromPrLink(prLink: string): string {
    const parts = prLink.split('/');
    if (parts.length < 7 || !prLink.includes('github.com')) {
        throw new Error(`Invalid GitHub PR link format: ${prLink}`);
    }
    return `${parts[3]}/${parts[4]}`;
}

export function extractOwnerAndRepoNameFromUrl(url:URL) {
    const splitted_paths = url.pathname.split("/")
    return {owner:splitted_paths[1],repo:splitted_paths[2]}
}
