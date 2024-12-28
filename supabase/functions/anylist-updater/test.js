// import AnyList from "npm:anylist@0.8.3";
import AnyList from "anylist";

const updateText = (text, quantityDiff) => {
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

Deno.serve(async (req) => {
    try {
        const payload = {
            type: "UPDATE",
            table: "inventory",
            record: {
                id: "4ae495e8-7761-41d2-99db-b91109e5dd8a",
                name: "ANYLIST API TEST",
                category: "wine-beer-spirits",
                quantity: 15,
                created_at: "2024-12-17T00:37:59.753309+00:00",
                description: "",
                modified_at: "2024-12-27T17:53:22.315826+00:00",
                anylist_identifier: "c9bd57c0bee24caeb5bfbde5241831ce"
            },
            schema: "public",
            old_record: {
                id: "4ae495e8-7761-41d2-99db-b91109e5dd8a",
                name: "ANYLIST API TEST",
                category: "wine-beer-spirits",
                quantity: 14,
                created_at: "2024-12-17T00:37:59.753309+00:00",
                description: "",
                modified_at: "2024-12-27T17:48:28.504015+00:00",
                anylist_identifier: "c9bd57c0bee24caeb5bfbde5241831ce"
            }
        };

        // console.log(req.json());

        // Only process UPDATE events
        if (payload.type !== "UPDATE") {
            return new Response(
                JSON.stringify({ message: "Only UPDATE events are processed" }),
                { status: 400 }
            );
        }

        const quantityDiff = payload.record.quantity - payload.old_record.quantity;

        if (Math.abs(quantityDiff) !== 1) {
            return new Response(
                JSON.stringify({ message: "Quantity must change by exactly 1" }),
                { status: 400 }
            );
        }

        const any = new AnyList({
            email: Deno.env.get("ANYLIST_EMAIL"),
            password: Deno.env.get("ANYLIST_PWD"),
        });

        console.log('starting');

        await any.login(false);
        await any.getLists();

        console.log('here');

        const shared_list = any.getListByName("Shared grocery list");
        const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);

        const existing_item = favorite_items.getItemById(
            payload.record.anylist_identifier
        );

        if (!existing_item) {
            await any.teardown();
            return new Response(
                JSON.stringify({ message: "Item not found in AnyList" }),
                { status: 404 }
            );
        }

        const updatedText = updateText(existing_item.details, quantityDiff);
        if (!updatedText) {
            await any.teardown();
            return new Response(
                JSON.stringify({ message: "Could not parse item details" }),
                { status: 400 }
            );
        }

        existing_item.details = updatedText;
        await existing_item.save();

        await any.teardown();

        return new Response(
            JSON.stringify({ message: "Successfully updated AnyList item" }),
            { status: 200 }
        );

    } catch (error) {
        return new Response(
            JSON.stringify({
                message: "Internal server error",
                error: error.message,
            }),
            { status: 500 }
        );
    }
});
