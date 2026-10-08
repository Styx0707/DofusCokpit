on(construct){
   while(true)
   {
      if(!(0x395829B3 & 0x395829B3))
      {
         if(!(0x395829B3 | 0x395829B3))
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
         backgroundRenderer = "UI_ExchangeGridBackground";
         set("\x16\x10\x12","");
         dragAndDrop = false;
         enabled = false;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_ExchangeGridHighlight");
         if(!(getTimer() + 1))
         {
            §§goto(addr5f4b3);
         }
      }
      set(§§pop(),§§pop());
      §§push("id");
      §§push(1);
      break;
   }
   set(§§pop(),§§pop());
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr5f4b3:
   §§pop()();
}
