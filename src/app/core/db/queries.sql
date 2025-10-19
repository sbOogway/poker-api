select h.player_id, count(*) as n_hands, sum(net_profit) as profit, sum(net_profit_before_rake) as profit_before_rake, 
	round(sum(vpip::int)::numeric / count(*) * 100, 2) as vpip,
	round(sum(preflop_raised::int)::numeric / count(*) * 100, 2) as pfr,
	round(sum(preflop_called::int)::numeric / count(*) * 100, 2) as pfc,
	round(sum(preflop_folded::int)::numeric / count(*) * 100, 2) as pff
from public.hand_player as h
where h.player_id  not like 'caduceus369'
group by h.player_id 
having count(*) > 150;