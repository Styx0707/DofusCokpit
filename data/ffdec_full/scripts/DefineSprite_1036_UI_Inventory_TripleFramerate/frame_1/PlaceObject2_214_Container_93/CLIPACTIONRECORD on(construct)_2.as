on(construct){
   while(true)
   {
      if(!ord("\x03"))
      {
         if(!ord("\x03"))
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
         if(false)
         {
            §§pop() extends §§pop();
            §§goto(addr2967);
         }
      }
      set(§§pop(),§§pop());
      §§push("margin");
      §§push(2);
      break;
   }
   set(§§pop(),§§pop());
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr2967:
}
