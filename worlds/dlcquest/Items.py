import csv
import enum
from typing import Protocol, Union, Dict, List
from BaseClasses import Item, ItemClassification
from . import Options, data
from dataclasses import dataclass, field

class DLCquestItem(Item):
    game: str = "DLCquest"

offset = 120_000



class Group(enum.Enum):
    DLC = enum.auto()
    DLCQuest = enum.auto()
    Freemium = enum.auto()
    Item = enum.auto()



@dataclass(frozen=True)
class ItemData:
    code_without_offset: offset
    name: str
    classification: ItemClassification
    groups: set[Group] = field(default_factory=frozenset)

    def __post_init__(self):
        if not isinstance(self.groups, frozenset):
            super().__setattr__("groups", frozenset(self.groups))

    @property
    def code(self):
        return offset + self.code_without_offset if self.code_without_offset is not None else None

    def has_any_group(self, *group: Group) -> bool:
        groups = set(group)
        return bool(groups.intersection(self.groups))

def load_item_csv():
    try:
        from importlib.resources import files
    except ImportError:
        from importlib_resources import files  # noqa

    items = []
    with files(data).joinpath("items.csv").open() as file:
        item_reader = csv.DictReader(file)
        for item in item_reader:
            id = int(item["id"]) if item["id"] else None
            classification = ItemClassification[item["classification"]]
            groups = {Group[group] for group in item["groups"].split(",") if group}
            items.append(ItemData(id, item["name"], classification, groups))
    return items

all_items: List[ItemData] = load_item_csv()
item_table: Dict[str, ItemData] = {}
items_by_group: Dict[Group, List[ItemData]] = {}
def initialize_item_table():
    item_table.update({item.name: item for item in all_items})

def initialize_groups():
    for item in all_items:
        for group in item.groups:
            item_group = items_by_group.get(group, list())
            item_group.append(item)
            items_by_group[group] = item_group


initialize_item_table()
initialize_groups()


def create_items(world, World_Options: Options.DLCQuestOptions):
    created_items = []
    if World_Options[Options.Campaign] == Options.Campaign.option_basic or World_Options[Options.Campaign] == Options.Campaign.option_both:
        for item in items_by_group[Group.DLCQuest]:
            created_items.append(world.create_item(item))
    if World_Options[Options.Campaign] == Options.Campaign.option_live_freemium_or_die or World_Options[Options.Campaign] == Options.Campaign.option_both:
        for item in items_by_group[Group.Freemium]:
            created_items.append(world.create_item(item))
    return created_items





