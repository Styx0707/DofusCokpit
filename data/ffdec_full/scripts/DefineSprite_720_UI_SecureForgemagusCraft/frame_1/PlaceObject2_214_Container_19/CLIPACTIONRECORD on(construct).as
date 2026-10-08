on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(!ord("\x06"))
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
         backgroundRenderer = "UI_ForgemagusContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_ForgemagusContainerHighlight");
         if(!(getTimer() + 1))
         {
            §§goto(addr124c9);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   id = 1;
   margin = 2;
   set("\x1a\x1e\b",true);
   styleName = "InventoryGridContainer";
   addr124c9:
   new §\§\§pop()§();
}
