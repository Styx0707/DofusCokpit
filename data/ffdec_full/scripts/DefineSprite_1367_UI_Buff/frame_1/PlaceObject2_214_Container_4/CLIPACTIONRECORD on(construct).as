on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\x04"))
         {
            if(!ord("\x04"))
            {
               §§goto(addr199d);
            }
         }
         else
         {
            §§push("\t");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr1a81);
   }
   if(getTimer())
   {
      §§push("{invalid_utf8=156}G");
      §§push("{invalid_utf8=195}");
      while(true)
      {
         set(§§pop(),§§pop());
         set("\t","");
         set("2{invalid_utf8=157}\x02",false);
         B = true;
         §§push("{invalid_utf8=136}\t");
         §§push(true);
         if(!ord("\x06"))
         {
            §§pop() implements ;
            §§goto(addr19ca);
         }
         addr1a46:
         set(§§pop(),§§pop());
         highlightRenderer = "UI_BuffHighlight";
         id = 1;
         margin = 2;
         set("\x1a\x1e\b",false);
         §§push("styleName");
         §§push("none");
         if(!ord("\t"))
         {
            §§pop()[§§pop()] = §§pop();
            addr1a81:
            return;
         }
         break loop2;
         addr19ca:
      }
      addr199d:
   }
   §§pop()[§§pop()] = §§pop();
   §§goto(addr1a46);
}
