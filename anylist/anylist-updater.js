const dotenv = require("dotenv");
const AnyList = require("../../anylist/lib/index");
const path = require('path')

// Parse arguments
const anylist_identifier = process.argv[2];
const quantity = parseInt(process.argv[3], 10);
const listName = "Shared grocery list";

function updateText(text, quantity) {
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
  const pattern = /(\d+)\s+(\D+)?\s?(\d{1,2}\/\d{1,2})/;
  const match = text.match(pattern);

  if (!match) {
    return null;
  }

  // Get the current quantity and increment it
  const currentQuantity = parseInt(match[1]);
  const newQuantity = currentQuantity + quantity;
  const noun = match[2];
  var updatedText = "";

  if (newQuantity > 0) {
    // Replace the old text with new values
    const spacing = noun ? ` ${noun} ` : ' ';
    updatedText = text.replace(
      pattern,
      `${newQuantity}${spacing}${currentDate}`,
    );
  } else {
    updatedText = text;
  }

  return updatedText;
}

async function updateItem(favorite_items, shared_list, anylist_identifier, quantity) {
  // updating favorite item
  let existing_item = favorite_items.getItemById(anylist_identifier);
  console.log(existing_item.name, existing_item.details);
  let updated_text = updateText(existing_item.details, quantity);
  console.log(updated_text);
  if (updateText == null) {
    return;
  }
  existing_item.details = updated_text;
  await existing_item.save(isFavorite = true);
  // check if favorite item in list
  // this is technically an edge case...
  // if there is an item in the list that is named exactly the same, there will be a conflict
  let duplicate_item = shared_list.getItemByName(existing_item.name);
  if (duplicate_item) {
    duplicate_item.details = updated_text;
    await duplicate_item.save();
  }
  return;
}

function updater(barcode, quantity) {
  dotenv.config({path:path.resolve(__dirname, '../anylist/.env')});
  const any = new AnyList({
    email: process.env.ANYLIST_EMAIL,
    password: process.env.ANYLIST_PWD,
  });

  any.login(connectWebSocket = false).then(async () => {
    await any.getLists();

    const shared_list = any.getListByName(listName);
    const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
    await updateItem(favorite_items, shared_list, anylist_identifier, quantity);
    // await item.save(isFavorite = true);
    // Clean up
    any.teardown();
    process.exit(0); // Explicitly exit the process
  });
}

updater(anylist_identifier, quantity);