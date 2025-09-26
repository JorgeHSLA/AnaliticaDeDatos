SELECT DISTINCT course_id
FROM indexador
WHERE palabra = 'salud';

SELECT course_id, COUNT(*) as repeticiones
FROM indexador
WHERE palabra = 'gestión'
GROUP BY course_id
ORDER BY repeticiones DESC;

SELECT DISTINCT course_id
FROM indexador
WHERE palabra IN ('salud', 'derecho', 'gestión');
