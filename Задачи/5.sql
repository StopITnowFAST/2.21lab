select
	timezone as Time_zone,
	count(*) as counter
from city
where
	timezone in ('UTC+3','UTC+4','UTC+5','UTC+6','UTC+7','UTC+8')
group by 1
order by 1;