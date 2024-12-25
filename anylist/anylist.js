const dotenv = require("dotenv");
const AnyList = require("../../anylist/lib/index");

function sortItems(favorite_items) {
  // Group items by category
  const groupedItems = favorite_items["items"].reduce((acc, item) => {
    const category = item._categoryMatchId;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push({ name: item._name, id: item._identifier });
    return acc;
  }, {});

  // Print categories and their items alphabetically
  for (const [category, items] of Object.entries(groupedItems)) {
    // Sort items alphabetically
    items.sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
    );
    items.forEach((item) =>
      console.log(`"${item["name"]}",${category},0,${item["id"]}`),
    );
  }
}

function updateText(text, expected_quantity) {
  // Get current date
  const today = new Date();
  const currentMonth = today.toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
    month: "2-digit",
  });
  const currentDay = today.toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
    day: "2-digit",
  });
  const currentDate = `${currentMonth}/${currentDay}`;

  // Extract the current quantity and noun
  const pattern = /(\d+)\s+(\w+)\s+(\d{1,2}\/\d{1,2})/;
  const match = text.match(pattern);

  if (!match) {
    return null;
  }

  // Get the current quantity and increment it
  const currentQuantity = parseInt(match[1]);
  const newQuantity = currentQuantity + 1;
  const noun = match[2];

  // Replace the old text with new values
  const updatedText = text.replace(
    pattern,
    `${newQuantity} ${noun} ${currentDate}`,
  );

  return updatedText;
}

function updateItem(favorite_items, anylist_identifier) {
  let existing_item = favorite_items.getItemById(anylist_identifier);
  console.log(existing_item.details);
  let updated_text = updateText(existing_item.details);
  console.log(updated_text);
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
  updateItem(favorite_items, "6a6ec1f358734b7283d57a49b9483b11");
  // console.log(favorite_items['items']);
  // sortItems(favorite_items);

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
