from typing import Optional, Iterable

"""
1. fantasy & sciencefiction
	2. fantasy
	3. sciencefiction
7. Romans
	21. Romance
	22. Historische romans
	23. Erotische romans
	24. Oorlogsromans
8. Kinderboeken
9. Geschiedenis
10. Wetenschap
	25. Biologie
	26. Wiskunde
	27. Scheikunde
	28. Sterrenkunde
	29. Natuurkunde
	30. Algemene wetenschap
11. Management
12. ICT
	13. Programmeren
	14. Systemen
15. Onderwijs en didactiek
16. Kookboeken
17. Hobby en vrije tijd
	19. Voertuigen
	20. Tuinieren
18. Theorie rij & vaarbewijzen
"""

class Genre:
    def __init__(self, pk: int, name: str, parent: Optional[int]=None):
        self.id = pk
        self.name = name
        self.parent = parent

genres = [
    Genre(1, 'Fantasy & Sciencefiction'),
        Genre(2, 'Fantasy', 1),
        Genre(3, 'Sciencefiction', 1),
    Genre(7, 'Romans'),
        Genre(21, 'Avontuur', 7),
        Genre(21, 'Romance', 7),
        Genre(22, 'Historische romans', 7),
        Genre(23, 'Erotische romans', 7),
        Genre(24, 'Oorlogsromans', 7),
        Genre(24, 'Western', 7),
    Genre(8, 'Kinderboeken'),
    Genre(9, 'Geschiedenis'),
    Genre(10, 'Wetenschap'),
        Genre(25, 'Biologie', 10),
        Genre(26, 'Wiskunde', 10),
        Genre(27, 'Scheikunde', 10),
        Genre(28, 'Sterrenkunde', 10),
        Genre(29, 'Algemene wetenschap', 10),
    Genre(11, 'Management'),
    Genre(12, 'ICT'),
        Genre(13, 'Programmeren', 12),
        Genre(14, 'Systemen', 12),
    Genre(15, 'Onderwijs & Didactiek'),
    Genre(16, 'Kookboeken'),
    Genre(17, 'Hobby & Vrije tijd'),
        Genre(19, 'Voertijgen', 17),
        Genre(20, 'Tuinieren', 17),
    Genre(18, 'Theorie rij- & vaarbewijzen')
]

def make_tree(data):
    tree = list()
    object_map = dict()

    for item in data:
        item_key = str(item.id)
        if item_key in object_map: continue
        object_map[item_key] = {
            'id': item.id,
            'name': item.name,
            'parent': item.parent,
            'children': list()
        }

    for key in object_map:
        item = object_map[key]
        if item['parent'] is None:
            tree.append(item)
        else:
            parent_key = str(item['parent'])
            object_map[parent_key]['children'].append(item)

    return tree

result = make_tree(genres)
print(result)