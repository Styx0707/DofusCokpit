on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x02");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         set("\x18\x07\x0e",true);
         highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
         §§push("id");
         §§push(1);
         if(!ord("\b"))
         {
            §§pop() extends §§pop();
            §§goto(addr60fc);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr60fc:
}
