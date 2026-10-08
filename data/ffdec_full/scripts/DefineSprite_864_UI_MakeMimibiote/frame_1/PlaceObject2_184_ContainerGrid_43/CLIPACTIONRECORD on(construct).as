on(construct){
   while(true)
   {
      if(!(0x1FAD80 | 0x1FAD80))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push("enabled");
         §§push(true);
      }
      set(§§pop(),§§pop());
      set("\x1a\x11\x11",false);
      selectable = false;
      break;
   }
   styleName = "ExchangeGrid";
   set("\x1b\x18\x02",1);
   set("\x1b\x18\x04",1);
}
