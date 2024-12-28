// Parse arguments
const barcode = process.argv[2];
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
  const pattern = /(\d+)\s+(\w+)\s+(\d{1,2}\/\d{1,2})/;
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
    updatedText = text.replace(
      pattern,
      `${newQuantity} ${noun} ${currentDate}`,
    );
  } else {
    updatedText = text;
  }

  return updatedText;
}

function updateItem(favorite_items, anylist_identifier, quantity) {
  let existing_item = favorite_items.getItemById(anylist_identifier);
  console.log(existing_item.details);
  let updated_text = updateText(existing_item.details, quantity);
  console.log(updated_text);
}

function updater(barcode, quantity) {
  dotenv.config();

  const any = new AnyList({
    email: process.env.ANYLIST_EMAIL,
    password: process.env.ANYLIST_PWD,
  });

  any.login().then(async () => {
    await any.getLists();

    const shared_list = any.getListByName(listName);
    const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
    updateItem(favorite_items, barcode, quantity);

    // Clean up
    any.teardown();
    process.exit(0); // Explicitly exit the process
  });
}

updater(barcode, quantity);