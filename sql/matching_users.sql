--- Query to generate recommendations

SELECT * FROM (
    SELECT 
        u.id, 
        COALESCE(lang_count, 0) as lang_score,
        COALESCE(interest_count, 0) as interest_score, 
        COALESCE(occupation_count, 0) as occupation_score, 
        COALESCE(skill_count, 0) as skill_score, 
        CASE
            WHEN cp.country_code = gp_current.country_code THEN 
                GREATEST(0, (:max_distance_kms - ST_DistanceSphere(cp.geolocation, gp_current.geolocation) / :meters_per_km) * :current_place_score_multiplier)
            ELSE 0
        END as current_place_score,
        CASE 
            WHEN op.country_code = gp_origin.country_code THEN 
                GREATEST(0, (:max_distance_kms - ST_DistanceSphere(op.geolocation, gp_origin.geolocation) / :meters_per_km) * :origin_place_score_multiplier)
            ELSE 0 
        END as origin_place_score,
        COALESCE(past_place_score, 0) as past_place_score,
        COALESCE(lang_count, 0) + 
        COALESCE(interest_count, 0) + 
        COALESCE(occupation_count, 0) + 
        COALESCE(skill_count, 0) + 
        CASE 
            WHEN cp.country_code = gp_current.country_code THEN 
                GREATEST(0, (:max_distance_kms - ST_DistanceSphere(cp.geolocation, gp_current.geolocation) / :meters_per_km) * :current_place_score_multiplier)
            ELSE 0 
        END +
        CASE 
            WHEN op.country_code = gp_origin.country_code THEN 
                GREATEST(0, (:max_distance_kms - ST_DistanceSphere(op.geolocation, gp_origin.geolocation) / :meters_per_km) * :origin_place_score_multiplier)
            ELSE 0 
        END +
        COALESCE(past_place_score, 0) AS total_match_score
    FROM 
        users u
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT language_id) AS lang_count
        FROM user_languages
        WHERE language_id IN (
            SELECT language_id
            FROM user_languages
            WHERE user_id = :given_user_id
        )
        GROUP BY user_id
    ) ul ON u.id = ul.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT interest_id) AS interest_count
        FROM user_interests
        WHERE interest_id IN (
            SELECT interest_id
            FROM user_interests
            WHERE user_id = :given_user_id
        )
        GROUP BY user_id
    ) ui ON u.id = ui.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT occupation_id) AS occupation_count
        FROM user_occupations
        WHERE occupation_id IN (
            SELECT occupation_id
            FROM user_occupations
            WHERE user_id = :given_user_id
        )
        GROUP BY user_id
    ) uo ON u.id = uo.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT skill_id) AS skill_count
        FROM user_skills
        WHERE skill_id IN (
            SELECT skill_id
            FROM user_skills
            WHERE user_id = :given_user_id
        )
        GROUP BY user_id
    ) us ON u.id = us.user_id
    LEFT JOIN places cp ON u.current_place_id = cp.id
    LEFT JOIN places op ON u.place_of_origin_id = op.id
    LEFT JOIN places gp_current ON gp_current.id = (
        SELECT current_place_id FROM users WHERE id = :given_user_id
    )
    LEFT JOIN places gp_origin ON gp_origin.id = (
        SELECT place_of_origin_id FROM users WHERE id = :given_user_id
    )
    LEFT JOIN (
        SELECT user_id, SUM(min_distance_score) as past_place_score
        FROM (
            SELECT upp.user_id, 
                CASE 
                    WHEN pp.country_code = ppp.country_code THEN 
                        GREATEST(0, (:max_distance_kms - MIN(ST_DistanceSphere(pp.geolocation, ppp.geolocation)) / :meters_per_km) * :past_place_score_multiplier) 
                    ELSE 0 
                END as min_distance_score
            FROM user_past_places upp
            INNER JOIN places pp ON upp.place_id = pp.id
            CROSS JOIN (
                SELECT places.id, places.geolocation, places.country_code
                FROM user_past_places
                INNER JOIN places ON user_past_places.place_id = places.id
                WHERE user_past_places.user_id = :given_user_id
            ) ppp
            WHERE ST_DistanceSphere(pp.geolocation, ppp.geolocation) <= :max_distance_meters
            GROUP BY upp.user_id, pp.id, pp.country_code, ppp.country_code
        ) as min_distances
        GROUP BY user_id
    ) past_place_scores ON u.id = past_place_scores.user_id
    LEFT JOIN user_connections uc ON (u.id = uc.connected_user_id AND uc.user_id = :given_user_id) OR (u.id = uc.user_id AND uc.connected_user_id = :given_user_id)
    WHERE u.id != :given_user_id AND uc.id IS NULL
    GROUP BY 
        u.id, 
        lang_count, 
        interest_count, 
        occupation_count, 
        skill_count, 
        cp.geolocation, 
        cp.country_code, 
        op.geolocation, 
        op.country_code,
        gp_origin.geolocation, 
        gp_origin.country_code,
        gp_current.geolocation, 
        gp_current.country_code,
        past_place_score
) AS main_query
WHERE main_query.total_match_score >= :min_score
ORDER BY main_query.total_match_score DESC
LIMIT :limit;
