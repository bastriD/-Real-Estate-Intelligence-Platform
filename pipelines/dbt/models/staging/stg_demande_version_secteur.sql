select demande_version_key, secteur_key
from {{ source('warehouse', 'bridge_demande_version_secteur') }}
