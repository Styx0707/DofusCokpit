on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(!(0x23D90078 & 0x23D90078))
         {
            break;
         }
      }
      else
      {
         §§push("\x06");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_InventoryContainerHighlight_TripleFramerate");
         if(!(getTimer() + 1))
         {
            §§goto(addrf80c);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addrf80c:
   §§pop()();
}
