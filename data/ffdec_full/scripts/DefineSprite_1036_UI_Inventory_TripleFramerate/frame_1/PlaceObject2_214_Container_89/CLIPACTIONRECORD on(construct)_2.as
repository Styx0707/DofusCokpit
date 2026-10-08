on(construct){
   while(true)
   {
      if(false)
      {
         if(!(true or true))
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
      highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
      §§push("margin");
      §§push(2);
      if(!getTimer())
      {
         duplicateMovieClip(§§pop(),§§pop(),§§pop());
         §§goto(addr602a);
      }
      break;
   }
   set(§§pop(),§§pop());
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr602a:
}
