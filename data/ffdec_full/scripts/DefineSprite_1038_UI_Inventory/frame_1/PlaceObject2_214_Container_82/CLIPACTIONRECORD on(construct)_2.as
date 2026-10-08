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
         §§push(236126769);
      }
      if(§§pop())
      {
         backgroundRenderer = "UI_InventoryContainerBackground";
         set("\x16\x10\x12","");
         dragAndDrop = true;
         enabled = true;
         §§push("\x18\x07\x0e");
         §§push(true);
         if(!ord("\b"))
         {
            §§goto(addr16caa);
         }
      }
      set(§§pop(),§§pop());
      highlightRenderer = "UI_InventoryContainerHighlight";
      §§push("margin");
      §§push(2);
      break;
   }
   set(§§pop(),§§pop());
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr16caa:
   getProperty(§§pop(), _X);
}
