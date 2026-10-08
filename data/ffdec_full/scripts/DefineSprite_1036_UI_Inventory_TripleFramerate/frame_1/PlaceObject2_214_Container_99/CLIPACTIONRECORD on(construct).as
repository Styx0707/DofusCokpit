on(construct){
   while(true)
   {
      if(!(0x21B2F145 & 0x21B2F145))
      {
         if(!(0x21B2F145 | 0x21B2F145))
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
         highlightRenderer = "UI_InventoryContainerHighlight_TripleFramerate";
         §§push("id");
         §§push(1);
         if(!ord("\x02"))
         {
            §§pop() extends §§pop();
            §§goto(addr19d4c);
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
   addr19d4c:
}
