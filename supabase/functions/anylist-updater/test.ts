import AnyList from "npm:anylist";

const updateText = (text: string, quantityDiff: number) => {
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

  const pattern = /(\d+)\s+(\w+)\s+(\d{1,2}\/\d{1,2})/;
  const match = text.match(pattern);
  if (!match) {
    return null;
  }

  const currentQuantity = parseInt(match[1]);
  const newQuantity = currentQuantity + quantityDiff;
  const noun = match[2];

  return text.replace(pattern, `${newQuantity} ${noun} ${currentDate}`);
};

serve(async (req) => {
  try {
    const payload = {'record': {'quantity': 5}, 'old_record': {'quantity: 4'}};

    // Calculate quantity difference
    const quantityDiff = payload.record.quantity - payload.old_record.quantity;

    // Only process if quantity changed by exactly 1 or -1
    if (Math.abs(quantityDiff) !== 1) {
      return new Response(
        JSON.stringify({ message: "Quantity must change by exactly 1" }),
        { status: 400 },
      );
    }

    // Initialize AnyList client
    const any = new AnyList({
      email: Deno.env.get("ANYLIST_EMAIL"),
      password: Deno.env.get("ANYLIST_PWD"),
    });

    console.log(any);

    // Login and get lists
    await any.login();
    await any.getLists();

    console.log('here');

    // Get shared list and favorite items
    const shared_list = any.getListByName("Shared grocery list");
    const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);

    // Get the specific item
    const existing_item = favorite_items.getItemById(
      payload.record.anylist_identifier,
    );

    if (!existing_item) {
      await any.teardown();
      return new Response(
        JSON.stringify({ message: "Item not found in AnyList" }),
        { status: 404 },
      );
    }

    // Update the text
    const updatedText = updateText(existing_item.details, quantityDiff);
    if (!updatedText) {
      await any.teardown();
      return new Response(
        JSON.stringify({ message: "Could not parse item details" }),
        { status: 400 },
      );
    }

    // Update the item in AnyList
    existing_item.details = updatedText;
    await existing_item.save();

    // Clean up
    await any.teardown();

    console.log('success');
  } catch (error) {
    console.log(error.message);
  }
});
