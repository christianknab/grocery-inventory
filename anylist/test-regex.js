const dotenv = require("dotenv");
const AnyList = require("../../anylist/lib/index");
const path = require('path')

const listName = "Shared grocery list";

function updateText(text) {
    const pattern = /((?:^|\n|\s)(\d+)(\s+[a-zA-Z]+)?\s+(\d{1,2}\/\d{1,2}))/;
    if (!text) return null;
    const match = text.match(pattern);

    if (!match) return null;

    const date = match[4];
    const currentQuantity = parseInt(match[2], 10);
    const noun = match[3] || '';

    return { currentQuantity, noun, date };
}

function updateItems(shared_list, quantity) {
    shared_list.items.forEach(item => {
        console.log(`Item: ${item._name}`);
        console.log(`Details: ${item._details}`);

        let updateResult = updateText(item._details);

        if (updateResult) {
            found = true;
            console.log(`Quantity: ${updateResult.currentQuantity}`);
            console.log(`Noun: ${updateResult.noun}`);
            console.log(`Date: ${updateResult.date}`);
        } else {
            console.log("NONE FOUND");
        }
        console.log(`\n`);
    });

    // for (const item of shared_list.items) {
    //     console.log(`Item: ${item.name}`);
    //     console.log(`Details: ${item.details}`);

    //     let updateResult = updateText(item.details, quantity);

    //     if (updateResult) {
    //         found = true;
    //         console.log(`Match 2: ${updateResult.newQuantity}`);
    //         console.log(`Match 3: ${updateResult.updatedText}`);
    //         console.log(`Match 4: ${updateResult.currentQuantity}`);
    //     } else {
    //         console.log("NONE FOUND");
    //     }
    // }
}

function updater(quantity) {
    dotenv.config({ path: path.resolve(__dirname, '../anylist/.env') });
    const any = new AnyList({ email: process.env.ANYLIST_EMAIL, password: process.env.ANYLIST_PWD });

    any.login(false).then(async () => {
        await any.getLists();
        const shared_list = any.getListByName(listName);
        const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
        updateItems(favorite_items, quantity);

        any.teardown();
        process.exit(0);
    }).catch((err) => {
        console.log(err);
        process.exit(1);
    });
}

updater(0);
