from common.Utils.unification_info import UnificationInfo, NotoriaUnificationInfo


class ParsingResult:
    def __init__(self, unification_info: [] = None, overlapping_info: {} = None):
        self.unification_info = unification_info
        if overlapping_info is None:
            self.overlapping_info = {}
        else:
            self.overlapping_info = overlapping_info

    def to_json(self):
        return UnificationInfo.list_to_json(self.unification_info)

    @staticmethod
    def combine_results(*results):
        unification_info = []
        for result in results:
            if result is not None:
                unification_info.extend(result.unification_info)

        if unification_info:
            return ParsingResult(unification_info)
        else:
            return None

    @staticmethod
    def combine_notoria_results(*results):
        unification_info = None

        for result in results:
            if result is not None:
                ui = result.unification_info[0]
                if unification_info is None:
                    company = ui.company
                    possible_matches = ui.possible_matches
                    unification_info = NotoriaUnificationInfo(company=company, possible_matches=possible_matches,
                                                              data=[])
                unification_info.data.extend(ui.data)

        if unification_info is not None:
            return ParsingResult([unification_info])
        else:
            return None
