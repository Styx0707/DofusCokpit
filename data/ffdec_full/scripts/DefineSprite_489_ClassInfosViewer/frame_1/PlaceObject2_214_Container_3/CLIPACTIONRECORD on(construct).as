on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!(0x2C308F49 & 0x2C308F49))
         {
            if(!ord("\x06"))
            {
               §§goto(addr6d45);
            }
         }
         else
         {
            §§push(917670800);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr6e43);
   }
   if(getTimer() + 1)
   {
      while(true)
      {
         set("{invalid_utf8=150}\x05","\x07{invalid_utf8=144}{invalid_utf8=139}{invalid_utf8=178}6{invalid_utf8=157}\x02");
         set("8","\x07{invalid_utf8=144}{invalid_utf8=139}{invalid_utf8=178}6{invalid_utf8=157}\x02");
         set("{invalid_utf8=136}\x04",true);
         set("\x01",true);
         §§push("&");
         §§push(true);
         if(!(getTimer() + 1))
         {
            §§pop() extends §§pop();
            §§goto(addr6d74);
         }
         addr6e08:
         set(§§pop(),§§pop());
         highlightRenderer = "ClassInfosViewerSpellContainerHighlight";
         id = 1;
         margin = 0;
         set("\x1a\x1e\b",false);
         §§push("styleName");
         §§push("none");
         if(!ord("\x05"))
         {
            setProperty(§§pop(), _X, §§pop());
            break;
         }
         break loop2;
         addr6d74:
      }
      addr6e43:
      return;
      addr6d45:
   }
   §§goto(addr6e08);
}
