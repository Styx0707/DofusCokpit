on(construct){
   while(true)
   {
      if(!(true or true))
      {
         if(!(true and true))
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
      §§push("\x18\x07\x0e");
      §§push(true);
      if(!(getTimer() + 1))
      {
         §§goto(addr1997a);
      }
      break;
   }
   set(§§pop(),§§pop());
   highlightRenderer = "UI_InventoryContainerHighlight";
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1997a:
   getProperty(§§pop(), _X);
}
