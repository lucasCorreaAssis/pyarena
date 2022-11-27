from typing import List
from promethee import Promethee, Criteria, UsualCurve

class ProductionOrderPriorization(Promethee):
    def __init__(self, alternatives: List[str]):
        criterias = self.__set_criterias()
        super().__init__(alternatives, criterias)

    def __set_criterias(self) -> List[Criteria]:
        criterias = list()

        Quality = Criteria(
            name='Quality',
            weight=0.28387,
            goal='min',
            curve=UsualCurve()
        )
        criterias.append(Quality) 

        Production = Criteria(
            name='Production',
            weight=0.03716,
            goal='min',
            curve=UsualCurve()
        )
        criterias.append(Production) 

        Avaibility = Criteria(
            name='Availability',
            weight=0.06964,
            goal='min',
            curve=UsualCurve()
        )
        criterias.append(Avaibility)

        MTTR = Criteria(
            name='MTTR',
            weight=0.32180,
            goal='max',
            curve=UsualCurve()
        )
        criterias.append(MTTR)

        MTBF = Criteria(
            name='MTBF',
            weight=0.28753,
            goal='min',
            curve=UsualCurve()
        )
        criterias.append(MTBF)

        return criterias