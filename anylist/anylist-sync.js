import { createClient } from "@supabase/supabase-js";
import AnyList from "../../anylist/lib/index.js";
import dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

const processAnyList = async () => {
  const any = new AnyList({
    email: process.env.ANYLIST_EMAIL,
    password: process.env.ANYLIST_PWD,
  });

  try {
    // Login to AnyList
    await any.login(false);

    // Fetch all lists and find the shared grocery list
    await any.getLists();
    const list = any.getListByName("Shared grocery list");
    if (!list) {
      console.error("Shared grocery list not found");
      return;
    }

    // Fetch favorite items from AnyList
    const favoriteItems = any.getFavoriteItemsByListId(list.identifier);
    const anylistIdentifiers = new Set(
      favoriteItems.items.map((item) => item.identifier)
    );

    // Fetch all inventory items from Supabase and store them in a Map
    const { data: inventory, error: inventoryError } = await supabase
      .from("inventory")
      .select("*");

    if (inventoryError) {
      console.error("Error fetching inventory:", inventoryError);
      return;
    }

    const inventoryMap = new Map(
      inventory.map((inv) => [inv.anylist_identifier, inv])
    );

    // Process AnyList items
    for (const item of favoriteItems.items) {
      const anylistId = item.identifier;
      const itemName = item.name;

      if (inventoryMap.has(anylistId)) {
        // Update name if it differs
        const existingItem = inventoryMap.get(anylistId);
        if (existingItem.name !== itemName) {
          console.log("UPDATING: ", itemName, anylistId);
          
          await supabase
            .from("inventory")
            .update({ name: itemName })
            .eq("anylist_identifier", anylistId);
          
        }
      } 
      else {
        // Check for matching name in inventory
        const nameMatch = Array.from(inventoryMap.values()).find(
          (inv) => inv.name === itemName
        );

        if (nameMatch) {
          // Update `anylist_identifier`
          console.log("UPDATING: ", nameMatch, anylistId);
          
          await supabase
            .from("inventory")
            .update({ anylist_identifier: anylistId })
            .eq("id", nameMatch.id);
          
        } else {
          // Insert a new row
          console.log("INSERTING: ", itemName, anylistId);
          
          await supabase
            .from("inventory")
            .insert({ name: itemName, anylist_identifier: anylistId });
          
        }
      }
    }

    // Remove items from Supabase that are not in AnyList
    const itemsToRemove = Array.from(inventoryMap.values()).filter(
      (inv) => !anylistIdentifiers.has(inv.anylist_identifier)
    );
    console.log(itemsToRemove);
    
    for (const item of itemsToRemove) {
      await supabase
        .from("inventory")
        .delete()
        .eq("id", item.id);
    }
    
  } catch (error) {
    console.error("Error:", error);
  } finally {
    // Cleanup before exiting
    any.teardown();
  }
};

processAnyList();
