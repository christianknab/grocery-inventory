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
  const pattern = /((?:^|\n|\s)(\d+)(\s+[a-zA-Z]+)?\s+(\d{1,2}\/\d{1,2}))/;
  const match = text.match(pattern);

  if (!match) {
    return null;
  }

  // Get the current quantity and increment it
  const fullMatch = match[1];  // full match with any space/newline padding
  const currentQuantity = parseInt(match[2], 10);
  const noun = match[3] || ''; // noun optional

  let newQuantity = currentQuantity + quantity;

  // Maintain original spacing/newlines
  var updatedText = "";

  if (newQuantity >= 0) {
    const updatedString = fullMatch.replace(
      /(\d+)(\s+[a-zA-Z]+)?\s*(\d{1,2}\/\d{1,2})/,
      `${newQuantity}${noun} ${currentDate}`
    );
    updatedText = text.replace(fullMatch, updatedString);
  } else {
    newQuantity = 0;
    updatedText = text;
  }

  return { updatedText, newQuantity, currentQuantity };
}

async function updateItem(favorite_items, shared_list, anylist_identifier, quantity, any) {
  try {
    let existing_item = favorite_items.getItemById(anylist_identifier);
    let updateResult = updateText(existing_item.details, quantity);

    if (!updateResult) {
      throw new Error(`${existing_item.name}\nInvalid quantity format!\nExisting item details:\n"${existing_item.details}"`);
    }
    old_details = existing_item.details;
    existing_item.details = updateResult.updatedText;
    await existing_item.save(true);

    // update if item in list
    let addedToList = false;
    let duplicate_item = shared_list.getItemByName(existing_item.name);
    if (duplicate_item) {
      duplicate_item.details = updateResult.updatedText;
      await duplicate_item.save();
    }
    // add to list if the inventory is 0
    else if (!duplicate_item && updateResult.newQuantity == 0) {
      // check first if the item's category is 'other'
      // if it is, there might be another category (the correct category) in the 'recent items' list
      let categoryMatchId = existing_item.categoryMatchId;
      const recent_items = any.getRecentItemsByListId(shared_list.identifier);
      recent_items.forEach(item => {
        if (item.name == existing_item.name) { if (item.categoryMatchId != 'other') { categoryMatchId = item.categoryMatchId; } }
      });
      // copy the item
      let new_item_data = {
        identifier: existing_item.identifier,
        name: existing_item.name,
        details: updateResult.updatedText,
        quantityPb: existing_item.quantityPb,
        checked: existing_item.checked,
        manualSortIndex: existing_item.manualSortIndex,
        userId: existing_item.userId,
        categoryMatchId: categoryMatchId,
        storeIds: existing_item.storeIds,
        photoIds: existing_item.photoIds,
        packageSizePb: existing_item.packageSizePb,
      };
      new_item = any.createItem(new_item_data);
      // let new_item = existing_item.copyWith();
      // new_item = any.createItem(existing_item);
      new_item = await shared_list.addItem(new_item);
      await new_item.save();
      addedToList = true;
    }

    console.log(JSON.stringify({
      status: "success",
      itemName: existing_item.name,
      newQuantity: updateResult.newQuantity,
      oldQuantity: updateResult.currentQuantity,
      newDetails: updateResult.updatedText,
      oldDetails: old_details,
      addedToList: addedToList,
    }));
  } catch (error) {
    console.log(JSON.stringify({
      status: "error",
      message: error.message
    }));
  }
}

function updater(barcode, quantity) {
  dotenv.config({ path: path.resolve(__dirname, '../anylist/.env') });
  const any = new AnyList({
    email: process.env.ANYLIST_EMAIL,
    password: process.env.ANYLIST_PWD,
  });
  any.login(false).then(async () => {
    await any.getLists();

    const shared_list = any.getListByName(listName);
    const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
    await updateItem(favorite_items, shared_list, anylist_identifier, quantity, any);

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
