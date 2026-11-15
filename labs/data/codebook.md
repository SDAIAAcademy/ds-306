# Sada complaint codebook (version 3)

Owner: Muhannad Al-Oqaili, head of complaint intake. Synthetic, for the DS-306 labs.

Assign **one** category to each complaint: the main problem the citizen asks the centre to fix. When a complaint
names two problems, the main one is the one described first and at more length. Do not code the tone.

| Code | Category | Includes | Does not include |
|---|---|---|---|
| `water_sewage` | Water and sewage (المياه والصرف الصحي) | Supply cuts, pressure, leaking pipes, sewage overflow, manholes, a street flooded by sewage or a burst pipe | Rain water on a damaged road with no pipe or sewage named (`roads`) |
| `roads` | Roads and pavements (الطرق والأرصفة) | Potholes, broken pavements, unfinished excavations, speed bumps, bridges | Road works that are noisy at night (`noise`) |
| `waste` | Waste and cleanliness (النظافة والنفايات) | Collection, bins, construction waste dumped | Dirty park toilets (`parks`) |
| `lighting` | Street lighting (إنارة الشوارع) | Lights off or on at the wrong time, leaning poles | Lighting inside a park (`parks`) |
| `noise` | Noise (الإزعاج والضوضاء) | Workshops, construction, halls, generators | |
| `permits` | Permits and licences (التصاريح والرخص) | Building permits, shop licences, licence inspections, rejections | Rude staff at a permits counter (`staff_service`) |
| `parks` | Parks and public facilities (الحدائق والمرافق العامة) | Play equipment, gardens, public toilets, walking tracks | |
| `staff_service` | Staff conduct and service (تعامل الموظفين وجودة الخدمة) | Rude staff, unanswered hotline, a report closed without action, waiting at a branch | A slow permit decision with no complaint about staff (`permits`) |

Coders work on redacted text. Personal data appears as `[PHONE]`, `[ID]`, `[EMAIL]` or `[NAME]`.
