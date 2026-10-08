on(construct){
   while(true)
   {
      if(!(0x062616E8 | 0x062616E8))
      {
         if(!ord("\x04"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(§§pop())
      {
         break;
      }
      backgroundRenderer = "UI_InventoryContainerBackground";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      §§push("highlightRenderer");
      §§push("UI_InventoryContainerHighlight");
      if(!(getTimer() + 1))
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         §§goto(addr1edba);
      }
      break;
   }
   set(§§pop(),§§pop());
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr1edba:
}
