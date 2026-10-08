on(construct){
   while(true)
   {
      if(!(0x07F76AA9 & 0x07F76AA9))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push(446582086);
      }
      if(§§pop())
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
            §§pop() extends §§pop();
            §§goto(addr0920);
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
   addr0920:
}
