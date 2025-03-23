SELECT EXISTS(SELECT 1 from pull_requests where repo='facebook/react') as repo_exists;

SELECT COUNT(*) AS total_prs FROM pull_requests;

SELECT COUNT(DISTINCT id) AS total_users FROM gh_users;

SELECT COUNT(*) AS total_reviews FROM pr_review;


SELECT 
  repo,
  COUNT(*) AS pr_count,
  COUNT(DISTINCT author_id) AS distinct_authors,
  AVG((
    SELECT COUNT(*) 
    FROM pr_review 
    WHERE pr_id = pull_requests.id
  )) AS avg_reviews_per_pr
FROM pull_requests
GROUP BY repo
ORDER BY pr_count DESC;


SELECT 
  u.username,
  COUNT(p.id) AS prs_created,
  COUNT(r.id) AS reviews_received
FROM gh_users u
LEFT JOIN pull_requests p ON u.id = p.author_id
LEFT JOIN pr_review r ON p.id = r.pr_id
GROUP BY u.id
ORDER BY prs_created DESC;


SELECT 
  u.username,
  COUNT(r.id) AS reviews_given,
  COUNT(DISTINCT r.pr_id) AS distinct_prs_reviewed
FROM gh_users u
LEFT JOIN pr_review r ON u.id = r.reviewer_id
GROUP BY u.id
ORDER BY reviews_given DESC;



SELECT 
  author.username AS pr_author,
  reviewer.username AS reviewer,
  COUNT(*) AS collaboration_count
FROM pr_review r
JOIN pull_requests p ON r.pr_id = p.id
JOIN gh_users author ON p.author_id = author.id
JOIN gh_users reviewer ON r.reviewer_id = reviewer.id
GROUP BY pr_author, reviewer
ORDER BY collaboration_count DESC;



SELECT 
  a.username AS user1,
  b.username AS user2,
  COUNT(*) AS reciprocal_count
FROM (
  SELECT p.author_id, r.reviewer_id
  FROM pr_review r
  JOIN pull_requests p ON r.pr_id = p.id
) AS relationships
JOIN gh_users a ON relationships.author_id = a.id
JOIN gh_users b ON relationships.reviewer_id = b.id
WHERE EXISTS (
  SELECT 1
  FROM pr_review r2
  JOIN pull_requests p2 ON r2.pr_id = p2.id
  WHERE p2.author_id = b.id
    AND r2.reviewer_id = a.id
)
AND a.id < b.id  -- Prevent duplicate pairs
GROUP BY user1, user2;


SELECT
  u.username,
  (SELECT COUNT(*) FROM pull_requests WHERE author_id = u.id) AS out_degree,
  (SELECT COUNT(*) FROM pr_review WHERE reviewer_id = u.id) AS in_degree
FROM gh_users u
ORDER BY (out_degree + in_degree) DESC;

SELECT
  u.username,
  COUNT(DISTINCT p.repo) AS projects_contributed_to,
  COUNT(DISTINCT r.pr_id) AS prs_reviewed
FROM gh_users u
LEFT JOIN pull_requests p ON u.id = p.author_id
LEFT JOIN pr_review r ON u.id = r.reviewer_id
GROUP BY u.id
HAVING projects_contributed_to > 1
ORDER BY projects_contributed_to DESC;


WITH collaboration_graph AS (
  SELECT
    p.author_id AS user1,
    r.reviewer_id AS user2,
    COUNT(*) AS weight
  FROM pr_review r
  JOIN pull_requests p ON r.pr_id = p.id
  GROUP BY user1, user2
)
SELECT 
  u1.username AS user_a,
  u2.username AS user_b,
  cg.weight AS collaboration_strength
FROM collaboration_graph cg
JOIN gh_users u1 ON cg.user1 = u1.id
JOIN gh_users u2 ON cg.user2 = u2.id
WHERE cg.weight > 3  -- Threshold for strong collaborations
ORDER BY cg.weight DESC;
-- These commands should be written in an sqlite terminal
.headers on
.mode csv
.output nodes.csv
SELECT 
  id AS node_id,
  username,
  (SELECT COUNT(*) FROM pull_requests WHERE author_id = id) AS pr_count,
  (SELECT COUNT(*) FROM pr_review WHERE reviewer_id = id) AS review_count
FROM gh_users;

-- Edges (Collaborations)
.output edges.csv
SELECT DISTINCT
  p.author_id AS source,
  r.reviewer_id AS target,
  'review' AS edge_type
FROM pr_review r
JOIN pull_requests p ON r.pr_id = p.id;
