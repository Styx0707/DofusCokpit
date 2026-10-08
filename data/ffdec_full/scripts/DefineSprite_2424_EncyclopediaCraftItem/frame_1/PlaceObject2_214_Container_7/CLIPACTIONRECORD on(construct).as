on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!ord("\x04"))
         {
            if(false)
            {
               while(true)
               {
                  set("\b\x07\b\x03\x1d{invalid_utf8=150}\x07","{invalid_utf8=136}\x04");
                  set("\b\b\x07\x01",1);
                  set("",2);
                  §§push("");
                  §§push(true);
                  if(!ord("\x05"))
                  {
                     §§goto(addr1e12d);
                     §§push(getProperty(§§pop(), _X));
                  }
                  §§goto(addr1e203);
                  break loop3;
               }
               §§goto(addr1e202);
               addr1e0fb:
            }
         }
         else
         {
            §§push(true);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 or _temp_1))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr1e0fb);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x02","\x05\x01L\x11{invalid_utf8=157}\x02");
      l = "{invalid_utf8=136}\x04";
      set("\x01",false);
      B = true;
      §§push("\x1d{invalid_utf8=150}\x04");
      §§push(false);
      break loop3;
      setProperty(§§pop(), _X, §§pop());
      §§goto(addr1e15f);
      addr1e15f:
   }
   break loop3;
   addr1e12d:
   addr1e202:
   §§pop() extends §§pop();
   addr1e203:
   set(§§pop(),§§pop());
   styleName = "InventoryGridContainer";
}
