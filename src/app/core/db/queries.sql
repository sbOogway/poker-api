-- see opponents stats
select h.player_id, count(*) as n_hands, sum(net_profit) as profit, sum(net_profit_before_rake) as profit_before_rake, 
	round(sum(vpip::int)::numeric / count(*) * 100, 2) as vpip,
	round(sum(preflop_raised::int)::numeric / count(*) * 100, 2) as pfr,
	round(sum(preflop_called::int)::numeric / count(*) * 100, 2) as pfc,
	round(sum(preflop_folded::int)::numeric / count(*) * 100, 2) as pff
from public.hand_player as h
where h.player_id  not like 'caduceus369'
group by h.player_id 
having count(*) > 150;

-- calculate ev on showdowns
select text, ev_pre, ev_flop, ev_turn, ev_river, ev_pre+ev_flop+ev_turn+ev_river as ev_total, net_profit
from hand h join hand_player hp on h.id = hp.hand_id  where (h.went_to_showdown is true and (h.text like '%' || :player_id || ' shows %' or h.text like '%' || :player_id  || ' mucks%' ))
UNION ALL
SELECT
    'TOTALS' AS text,
    SUM(ev_pre) AS ev_pre,
    SUM(ev_flop) AS ev_flop,
    SUM(ev_turn) AS ev_turn,
    SUM(ev_river) AS ev_river,
    SUM(ev_pre + ev_flop + ev_turn + ev_river) AS ev_total,
    SUM(net_profit) AS net_profit
FROM hand h
JOIN hand_player hp ON h.id = hp.hand_id
WHERE
    h.went_to_showdown IS TRUE
    AND (
        h.text LIKE '%' || :player_id || ' shows %'
        OR h.text LIKE '%' || :player_id || ' mucks%'
    );
   
   ORDER BY CASE WHEN text = 'TOTALS' THEN 1 ELSE 0 END, text;