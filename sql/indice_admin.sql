SET search_path TO projeto_f1;

-- ============================================================
-- Índices para buscar aeroportos próximos de uma cidade no Brasil
-- ============================================================

-- Ajuda a localizar a cidade pesquisada pelo nome normalizado
-- A consulta usa LOWER + TRIM + TRANSLATE, então o índice replica a expressão usada na função.
CREATE INDEX IF NOT EXISTS idx_cities_country_nome_normalizado
ON cities (
    country_id,
    (
        TRANSLATE(
            LOWER(TRIM(name)),
            'áàãâäéèêëíìîïóòõôöúùûüç',
            'aaaaaeeeeiiiiooooouuuuc'
        )
    )
)
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL;

-- Ajuda a encontrar aeroportos pela cidade e pelo tipo.
-- Também limita aos aeroportos que têm coordenadas, pois a consulta só usa esses.
CREATE INDEX IF NOT EXISTS idx_airports_city_type_coords
ON airports(city_id, airport_type_id)
WHERE latitude_deg IS NOT NULL
  AND longitude_deg IS NOT NULL;


-- Ajuda no filtro por tipo de aeroporto: medium_airport e large_airport.
CREATE INDEX IF NOT EXISTS idx_airport_types_type
ON airport_types(type);