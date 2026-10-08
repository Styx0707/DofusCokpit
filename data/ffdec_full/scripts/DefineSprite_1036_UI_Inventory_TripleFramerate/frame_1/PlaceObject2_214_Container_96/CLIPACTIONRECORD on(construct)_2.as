on(construct){
   while(true)
   {
      if(!ord("\x0b"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 or _temp_1))
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
      §§push("margin");
      §§push(2);
      if(!getTimer())
      {
         §§pop() extends §§pop();
      }
      else
      {
         addr185d:
         set(§§pop(),§§pop());
         set("\x1a\x1e\b",false);
         styleName = "default";
      }
      return;
   }
   §§goto(addr185d);
}
