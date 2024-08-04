const dotenv = require("dotenv");
const AnyList = require("../anylist-api/anylist/lib/index");

dotenv.config();

const any = new AnyList({
  email: process.env.ANYLIST_EMAIL,
  password: process.env.ANYLIST_PWD,
});

any.login().then(async () => {
  await any.getLists();

  const shared_list = any.getListByName("Shared grocery list");
  const favorite_items = any.getFavoriteItemsByListId(shared_list.identifier);
  // for (const item of favorite_items) {
  //   console.log(item.name);
  // }
  let item = favorite_items.getItemByName("campanelle");
  console.log(item);
  // let garlic = shared_list.getItemByName("Rice Krispies");
  // console.log(garlic);
  // garlic.details = "1 heads 8/3";
  // await garlic.save();
  // Clean up
  any.teardown();
});
