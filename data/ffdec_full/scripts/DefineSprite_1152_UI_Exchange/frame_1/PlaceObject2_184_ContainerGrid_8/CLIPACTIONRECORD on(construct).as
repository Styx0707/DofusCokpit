on(construct){
   while(true)
   {
      if(!(0x1577C031 | 0x1577C031))
      {
         if(false)
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
         enabled = true;
         set("\x1a\x11\x11",true);
         selectable = true;
         styleName = "ExchangeGrid";
         §§push("\x1b\x18\x02");
         §§push(7);
         if(!ord("\n"))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr2d965);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x1b\x18\x04",2);
   addr2d965:
}
