import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def plot_degree_distributions_per_repo(repos_df, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for repo in repos_df["Package"]:
        cursor.execute("""
            SELECT DISTINCT gh.id
            FROM gh_users gh
            JOIN pull_requests pr ON gh.id = pr.author_id
            WHERE pr.repo = ? AND gh.username NOT LIKE '%[bot]%'
        """, (repo,))
        author_ids = set(row[0] for row in cursor.fetchall())

        cursor.execute("""
            SELECT DISTINCT gh.id
            FROM gh_users gh
            JOIN pr_review r ON gh.id = r.reviewer_id
            JOIN pull_requests p ON r.pr_id = p.id
            WHERE p.repo = ? AND gh.username NOT LIKE '%[bot]%'
        """, (repo,))
        reviewer_ids = set(row[0] for row in cursor.fetchall())

        all_users = author_ids | reviewer_ids
        if not all_users:
            continue

        G = nx.DiGraph()
        G.add_nodes_from(all_users)

        cursor.execute("""
            SELECT p.author_id, r.reviewer_id
            FROM pr_review r
            JOIN pull_requests p ON r.pr_id = p.id
            JOIN gh_users a ON p.author_id = a.id
            JOIN gh_users b ON r.reviewer_id = b.id
            WHERE p.repo = ? AND a.username NOT LIKE '%[bot]%' AND b.username NOT LIKE '%[bot]%'
                  AND p.author_id != r.reviewer_id
        """, (repo,))
        edges = [(a, b) for a, b in cursor.fetchall() if a in all_users and b in all_users]
        G.add_edges_from(edges)

        if G.number_of_edges() == 0:
            continue

        in_degrees = [G.in_degree(n) for n in G.nodes()]
        out_degrees = [G.out_degree(n) for n in G.nodes()]

        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        ax[0].hist(in_degrees, bins=range(1, max(in_degrees) + 2), density=True, color='steelblue', edgecolor='black')
        ax[0].set_title(f"{repo} - Normalized In-Degree Distribution")
        ax[0].set_xlabel("In-Degree (k)")
        ax[0].set_ylabel("P(k)")

        ax[1].hist(out_degrees, bins=range(1, max(out_degrees) + 2), density=True, color='salmon', edgecolor='black')
        ax[1].set_title(f"{repo} - Normalized Out-Degree Distribution")
        ax[1].set_xlabel("Out-Degree (k)")
        ax[1].set_ylabel("P(k)")

        plt.tight_layout()
        safe_repo_name = repo.replace("/", "_")
        plt.savefig(f"{safe_repo_name}_degree_distribution.pdf")
        plt.close()

    conn.close()

# Example usage
df = pd.DataFrame({"Package": ['vuejs/core', 'facebook/react', 'angular/angular-cli']})
plot_degree_distributions_per_repo(df, "../data-collection/github-data-latest.db")