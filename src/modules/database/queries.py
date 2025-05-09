get_ops_between_dates = """
SELECT
    o.ID AS [id],
    o.oper_date AS [date],
    u.emp_id AS [emp_id],
    u.first_name AS [name],
    u.last_name AS [lastname],
    t.name AS [terminal],
    o.credit_block AS [block]
FROM
    ven_operations o
INNER JOIN
    ven_users u ON o.user_id = u.ID
INNER JOIN
    ven_terminals t ON o.terminal_id = t.ID
WHERE
    o.oper_date BETWEEN ? AND ?
ORDER BY
    o.oper_date DESC;
"""
