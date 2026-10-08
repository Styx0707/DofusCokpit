on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(0x10F8CC89 | 0x10F8CC89))
         {
            if(false)
            {
               while(true)
               {
                  set(§§pop(),§§pop());
                  set("",0);
                  set("",4);
                  set("\x1d{invalid_utf8=150}\x07",0);
                  §§push("\b\r\x07\x04");
                  §§push(0);
                  if(!(getTimer() + 1))
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addr4f22);
                  }
                  §§goto(addr4f68);
                  break loop3;
               }
               §§goto(addr5097);
               addr4eee:
            }
         }
         else
         {
            §§push(185359114);
         }
         if(!§§pop())
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr4eee);
   }
   do
   {
      set("{invalid_utf8=150}\x05","\x07\n[\f\x0b{invalid_utf8=157}\x02");
      set("{invalid_utf8=193}","{invalid_utf8=136}\b");
      set("\x02","{invalid_utf8=136}\b");
      set("{invalid_utf8=130}{invalid_utf8=135}","9)");
      set("\x1d{invalid_utf8=150}\x04",20);
      set("\b\x0b\x05","\x1d{invalid_utf8=150}\x07");
      §§push("\b\f\x01");
      §§push(true);
      break loop3;
      duplicateMovieClip(§§pop(),§§pop(),§§pop());
      set(§§pop(),§§pop());
      set("",4);
      set("",4);
      set("\x1d{invalid_utf8=150}\x07","\b\x0e\x01");
      §§push("");
      §§push(3);
      if(false)
      {
         §§push(§§pop()(§§pop()));
      }
      else
      {
         §§goto(addr5098);
      }
   }
   while(true);
   addr4f22:
   addr5097:
   §§pop()[§§pop()] = §§pop();
   addr5098:
   set(§§pop(),§§pop());
   rowHeight = 20;
   styleName = "OrangeComboBox";
}
