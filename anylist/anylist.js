const dotenv = require("dotenv");
const AnyList = require("../../anylist/lib/index");

function sortItems(favorite_items) {
  // Group items by category
  const groupedItems = favorite_items['items'].reduce((acc, item) => {
    const category = item._categoryMatchId;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push({'name': item._name, 'id': item._identifier});
    return acc;
  }, {});

  // Print categories and their items alphabetically
  for (const [category, items] of Object.entries(groupedItems)) {
    // Sort items alphabetically
    items.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }));
    items.forEach(item => console.log(`"${item['name']}",${category},0,${item['id']}`));
  }
}

dotenv.config();

const any = new AnyList({
  email: process.env.ANYLIST_EMAIL,
  password: process.env.ANYLIST_PWD,
});

any.login().then(async () => {
  await any.getLists();

  const shared_list = any.getListByName("Shared grocery list");
  const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);

  // console.log(favorite_items['items']);
  sortItems(favorite_items);

  // let existing_item = favorite_items.getItemByName("ANYLIST API TEST");
  // existing_item.details = "updated detail 1";
  // await existing_item.save(isFavorite=true);

  // let test_add = any.createItem({name: 'test4', category: 'other'});
  // await favorite_items.addItem(test_add, true);

  // let test_delete = favorite_items.getItemByName("test4");
  // await favorite_items.removeItem(test_delete, true);

  // Clean up
  any.teardown();
  process.exit(0); // Explicitly exit the process
});
