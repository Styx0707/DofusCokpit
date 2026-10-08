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
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         while(true)
         {
            if(!(getTimer() + 1))
            {
               setProperty(§§pop(), _X, §§pop());
               break;
            }
            backgroundRenderer = "";
            set("\x16\x10\x12","");
            dragAndDrop = false;
            enabled = true;
            set("\x18\x07\x0e",true);
            §§push("highlightRenderer");
            §§push("UI_BuffHighlight");
            if(!(getTimer() + 1))
            {
               continue;
            }
            §§push(new §\§\§pop()§());
         }
         §§goto(addre303);
      }
      set(§§pop(),§§pop());
      §§push(§§constant(8));
      §§push(1);
      break;
   }
   set(§§pop(),§§pop());
   set("d|",2);
   set("\x1d{invalid_utf8=150}\x07",false);
   set("\b\b\x07\x01","");
   addre303:
}
