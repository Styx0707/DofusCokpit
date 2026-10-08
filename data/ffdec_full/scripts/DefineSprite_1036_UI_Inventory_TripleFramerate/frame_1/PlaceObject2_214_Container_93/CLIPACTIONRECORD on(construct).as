on(construct){
   while(true)
   {
      if(!ord("\x03"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_InventoryContainerHighlight_TripleFramerate");
         if(!getTimer())
         {
            §§goto(addr326c);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr326c:
   getProperty(§§pop(), _X);
}
