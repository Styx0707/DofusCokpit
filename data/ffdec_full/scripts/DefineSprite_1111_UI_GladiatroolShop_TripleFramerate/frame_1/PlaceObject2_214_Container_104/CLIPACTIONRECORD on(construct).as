on(construct){
   while(true)
   {
      if(!(true and true))
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
         backgroundRenderer = "UI_ExchangeGridBackground";
         set("\x16\x10\x12","");
         dragAndDrop = false;
         enabled = false;
         set("\x18\x07\x0e",true);
         §§push("highlightRenderer");
         §§push("UI_ExchangeGridHighlight");
         if(!ord("\x02"))
         {
            §§goto(addrbd6a);
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
   addrbd6a:
   new §\§\§pop()§();
}
