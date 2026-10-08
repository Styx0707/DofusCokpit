on(construct){
   while(true)
   {
      if(!(0x2A4971F4 & 0x2A4971F4))
      {
         if(!ord("\x06"))
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
      set("\x1a\x11\x11",true);
      selectable = true;
      §§push("styleName");
      §§push("CustomSetGrid");
      break;
   }
   set(§§pop(),§§pop());
   set("\x1b\x18\x02",4);
   set("\x1b\x18\x04",2);
}
