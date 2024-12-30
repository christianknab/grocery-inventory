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

  return { updatedText, newQuantity, currentQuantity };
}

async function updateItem(favorite_items, shared_list, anylist_identifier, quantity) {
  try {
    let existing_item = favorite_items.getItemById(anylist_identifier);
    let updateResult = updateText(existing_item.details, quantity);
    
    if (!updateResult) {
      throw new Error("Failed to match item details format.");
    }
    
    existing_item.details = updateResult.updatedText;
    await existing_item.save(true);

    let duplicate_item = shared_list.getItemByName(existing_item.name);
    if (duplicate_item) {
      duplicate_item.details = updateResult.updatedText;
      await duplicate_item.save();
    }

    console.log(JSON.stringify({
      status: "success",
      itemName: existing_item.name,
      newQuantity: updateResult.newQuantity,
      oldQuantity: updateResult.currentQuantity
    }));
  } catch (error) {
    console.log(JSON.stringify({
      status: "error",
      message: error.message
    }));
  }
}

function updater(barcode, quantity) {
  dotenv.config({path:path.resolve(__dirname, '../anylist/.env')});
  const any = new AnyList({
    email: process.env.ANYLIST_EMAIL,
    password: process.env.ANYLIST_PWD,
  });

  any.login(false).then(async () => {
    await any.getLists();

    const shared_list = any.getListByName(listName);
    const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
    await updateItem(favorite_items, shared_list, anylist_identifier, quantity);

    any.teardown();
    process.exit(0);
  }).catch((err) => {
    console.log(JSON.stringify({
      status: "error",
      message: "Failed to login or retrieve lists."
    }));
    process.exit(1);
  });
}

updater(anylist_identifier, quantity);
