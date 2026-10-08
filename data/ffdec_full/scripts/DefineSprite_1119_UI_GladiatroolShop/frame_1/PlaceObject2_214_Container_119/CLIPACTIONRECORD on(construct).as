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
         §§push("\x07");
      }
      if(ord(§§pop()))
      {
         backgroundRenderer = "UI_ExchangeGridBackground";
         set("\x16\x10\x12","");
         dragAndDrop = false;
         enabled = true;
         set("\x18\x07\x0e",true);
         highlightRenderer = "UI_ExchangeGridHighlight";
         §§push("id");
         §§push(1);
         if(false)
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr35b98);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   margin = 2;
   set("\x1a\x1e\b",false);
   styleName = "default";
   addr35b98:
}
