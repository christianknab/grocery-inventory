// const dotenv = require("dotenv");
// const AnyList = require("../../anylist/lib/index");
// const fs = require('fs');

// const listName = "Shared grocery list";

// dotenv.config();

// const any = new AnyList({
//   email: process.env.ANYLIST_EMAIL,
//   password: process.env.ANYLIST_PWD,
// });

// any.login(connectWebSocket = false).then(async () => {
//   await any.getLists();
//   const list = any.getListByName("Shared grocery list");
//   // list.items.forEach(item => {
//   //   console.log(item._name)
//   //   console.log(item._protobuf)


//   // });

//   list.items.forEach(item => {
//     console.log(item._name);

//     // Check if the item has raw protobuf data to decode
//     if (item._protobuf && item._protobuf.decode && item._protobufData) {
//       const decoded = item._protobuf.decode(item._protobufData);
//       console.log(decoded);  // Print the decoded protobuf object
//     } else {
//       console.log(item._protobuf);  // Fallback if no data exists
//     }
//   });


//   //   console.log("LIST")
//   //   console.log(list)
//   //   console.log("DECODEDDDD")
//   //   list.items.forEach(item => {
//   //     // Decode the protobuf object
//   //     if (item._protobuf && item._protobuf.decode) {
//   //         const decoded = item._protobuf.decode(item._protobuf);
//   //         console.log(decoded);
//   //     } else {
//   //         console.log(item);
//   //     }
//   // });

//   // const favorite_items = any.getFavoriteItemsByListId(list.identifier);
//   // console.log("FAVORITES")
//   // // console.log(favorite_items)

//   // favorite_items.items.forEach(item => {
//   //   console.log(item._name)
//   //   console.log(item._protobuf)
//   // });





//   // const shared_list = any.getListByName(listName);
//   // const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
//   // const item = updateItem(favorite_items, anylist_identifier, quantity);
//   // await item.save(isFavorite = true);
//   // Clean up
//   any.teardown();
//   process.exit(0); // Explicitly exit the process
// });
