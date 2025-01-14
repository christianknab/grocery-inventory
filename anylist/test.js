const dotenv = require("dotenv");
const AnyList = require("../../anylist/lib/index");
const fs = require('fs');

const listName = "Shared grocery list";

dotenv.config();

const any = new AnyList({
  email: process.env.ANYLIST_EMAIL,
  password: process.env.ANYLIST_PWD,
});

any.login(connectWebSocket = false).then(async () => {
  await any.getLists();
  const list = any.getListByName("Shared grocery list");


  // const list = any.getListByName("Recent Items");
  // console.log(list);
  // const recent_items = any.getRecentItemsByListId(list.identifier);
  // // console.log(recent_items)
  // recent_items.forEach(item => {
  //   if (item.name == "Spray n Wash") { if (item.categoryMatchId != 'other') {console.log(item)} }
  // });



  const favorite_items = any.getFavoriteItemsByListId(list.identifier);
  //   console.log("FAVORITES")
  // console.log(favorite_items)

    favorite_items.items.forEach(item => {
      console.log(item)
      // console.log(item._protobuf)
    });





  // const shared_list = any.getListByName(listName);
  // const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
  // const item = updateItem(favorite_items, anylist_identifier, quantity);
  // await item.save(isFavorite = true);
  // Clean up
  any.teardown();
  process.exit(0); // Explicitly exit the process
});